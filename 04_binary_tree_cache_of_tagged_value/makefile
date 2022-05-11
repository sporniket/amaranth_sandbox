
sources_utils=cli_sporny.py
sources_modules=CellOfTaggedValue.py BinaryTreeCacheOfTaggedValue.py
sources_top=BinaryTreeCacheOfTaggedValue.py

%.vcd: %.py $(sources_utils)
	python3 $< simulate -v $@ -c 20

%.gtkw: %.py $(sources_utils)
	python3 $< simulate -v $@ -c 20

%.il: %.py $(sources_utils)
	@echo "########################################[ START VERIFY $< ]"
	python3 $< generate -t il $@
	cp $@ __test.il
	sby -f test.sby
	@echo "########################################[ END VERIFY $< ]"

.PHONY: simulations verifications

simulations: $(sources_modules:.py=.vcd) $(sources_modules:.py=.gtkw)

verifications: $(sources_modules:.py=.il)
